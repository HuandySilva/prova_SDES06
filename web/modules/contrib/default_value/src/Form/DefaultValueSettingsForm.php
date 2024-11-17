<?php

namespace Drupal\default_value\Form;

use Drupal\Core\Database\Connection;
use Drupal\Core\Entity\ContentEntityBase;
use Drupal\Core\Entity\EntityTypeBundleInfo;
use Drupal\Core\Entity\EntityTypeManagerInterface;
use Drupal\Core\Form\ConfigFormBase;
use Drupal\Core\Form\FormStateInterface;
use Symfony\Component\DependencyInjection\ContainerInterface;
use Symfony\Component\HttpFoundation\Request;

/**
 * Defines a form that configures default_value settings.
 */
class DefaultValueSettingsForm extends ConfigFormBase {

  /**
   * Entity Type Manager.
   *
   * @var \Drupal\Core\Entity\EntityTypeManagerInterface
   */
  protected $entityTypeManager;

  /**
   * Entity Bundle Info.
   *
   * @var \Drupal\Core\Entity\EntityTypeBundleInfo
   */
  protected $bundleInfo;

  /**
   * Database connection.
   *
   * @var \Drupal\Core\Database\Connection
   */
  protected $database;

  /**
   * Supported Entities.
   *
   * @var array
   */
  protected $supportedEntities;

  /**
   * Constructs a new SettingsForm object.
   *
   * @param \Drupal\Core\Entity\EntityTypeManagerInterface $entityTypeManager
   *   Entity Type Manager.
   * @param \Drupal\Core\Entity\EntityTypeBundleInfo $bundleInfo
   *   Entity Bundle Info.
   * @param \Drupal\Core\Database\Connection $database
   *   Database connection.
   */
  public function __construct(EntityTypeManagerInterface $entityTypeManager, EntityTypeBundleInfo $bundleInfo, Connection $database) {
    $this->entityTypeManager = $entityTypeManager;
    $this->bundleInfo = $bundleInfo;
    $this->database = $database;
    $this->setSupporrtedEntities();
  }

  /**
   * {@inheritdoc}
   */
  public static function create(ContainerInterface $container) {
    return new static(
      $container->get('entity_type.manager'),
      $container->get('entity_type.bundle.info'),
      $container->get('database'),
    );
  }

  /**
   * {@inheritdoc}
   */
  public function getFormId() {
    return 'default_value_settings_form';
  }

  /**
   * {@inheritdoc}
   */
  protected function getEditableConfigNames() {
    return [
      'default_value.settings',
    ];
  }

  /**
   * {@inheritdoc}
   */
  public function buildForm(array $form, FormStateInterface $form_state, Request $request = NULL) {
    $config = $this->config('default_value.settings');
    foreach ($this->supportedEntities as $entityTypeID => $entityTypeInfo) {
      $group_id = 'fs_' . $entityTypeID;
      $form[$group_id] = [
        '#type' => 'fieldset',
        '#title' => $entityTypeInfo['label'],
      ];
      $params = [
        '@bundle' => $entityTypeInfo['bundles']['label'],
      ];
      $form[$group_id][$entityTypeID] = [
        '#type' => 'checkboxes',
        '#title' => $this->t('Select @bundle for apply default value from field configuration.', $params),
        '#options' => $entityTypeInfo['bundles']['options'],
        '#default_value' => is_array($config->get($entityTypeID)) ? $config->get($entityTypeID) : [],
      ];
    }

    return parent::buildForm($form, $form_state);
  }

  /**
   * {@inheritdoc}
   */
  public function submitForm(array &$form, FormStateInterface $form_state) {
    $values = $form_state->getValues();
    $config = $this->config('default_value.settings');
    foreach ($this->supportedEntities as $entityTypeID => $entityTypeInfo) {
      $config->set($entityTypeID, $values[$entityTypeID]);
    }
    $config->save();
    if ($this->database->schema()->tableExists('cache_entity')) {
      $this->database->truncate('cache_entity')->execute();
    }
    if ($this->database->schema()->tableExists('cache_render')) {
      $this->database->truncate('cache_render')->execute();
    }
    if ($this->database->schema()->tableExists('cache_menu')) {
      $this->database->truncate('cache_menu')->execute();
    }
    if ($this->database->schema()->tableExists('cache_page')) {
      $this->database->truncate('cache_page')->execute();
    }
    if ($this->database->schema()->tableExists('cache_dynamic_page_cache')) {
      $this->database->truncate('cache_dynamic_page_cache')->execute();
    }
    parent::submitForm($form, $form_state);
  }

  /**
   * {@inheritdoc}
   */
  public function setSupporrtedEntities() {
    $notInclude = [
      'path_alias',
      'webform_submission',
      'contact_message',
      'shortcut',
      'search_api_task',
      'redirect',
      'file',
    ];
    $entities = $this->entityTypeManager->getDefinitions();
    foreach ($entities as $entityTypeID => $entityType) {
      if (in_array($entityTypeID, $notInclude)) {
        continue;
      }
      if ($entityType->entityClassImplements(ContentEntityBase::class)) {
        $bundles = $this->bundleInfo->getBundleInfo($entityTypeID);
        $bundle_options = [];
        foreach ($bundles as $key => $value) {
          $bundle_options[$key] = $value['label'];
        }
        $this->supportedEntities[$entityTypeID]['label'] = $entityType->getLabel();
        $this->supportedEntities[$entityTypeID]['bundles']['label'] = $entityType->getBundleLabel();
        $this->supportedEntities[$entityTypeID]['bundles']['options'] = $bundle_options;
      }
    }
  }

}
